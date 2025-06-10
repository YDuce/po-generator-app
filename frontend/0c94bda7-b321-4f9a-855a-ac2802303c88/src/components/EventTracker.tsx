import React from 'react';
import { CalendarIcon, PlusIcon, BellIcon, AlertCircleIcon } from 'lucide-react';
export function EventTracker() {
  const events = [{
    id: 1,
    title: 'Amazon Prime Day',
    date: '2024-07-11',
    type: 'Sale Event',
    status: 'Upcoming',
    description: 'Major sales event. Increase inventory by 50%'
  }, {
    id: 2,
    title: 'Holiday Season Prep',
    date: '2024-11-01',
    type: 'Inventory',
    status: 'Planning',
    description: 'Begin holiday inventory stocking'
  }, {
    id: 3,
    title: 'Black Friday',
    date: '2024-11-29',
    type: 'Sale Event',
    status: 'Planning',
    description: 'Prepare promotional inventory and pricing'
  }, {
    id: 4,
    title: 'Q1 Inventory Review',
    date: '2024-03-31',
    type: 'Review',
    status: 'Completed',
    description: 'Quarterly inventory assessment'
  }];
  const upcomingEvents = events.filter(event => event.status === 'Upcoming');
  const planningEvents = events.filter(event => event.status === 'Planning');
  const completedEvents = events.filter(event => event.status === 'Completed');
  return <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Event Tracker</h1>
        <button className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center space-x-2 hover:bg-blue-700 transition-colors">
          <PlusIcon className="w-4 h-4" />
          <span>Add Event</span>
        </button>
      </div>
      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center space-x-3">
            <div className="p-3 rounded-full bg-blue-100">
              <BellIcon className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600">
                Upcoming Events
              </p>
              <p className="text-2xl font-bold text-gray-900">
                {upcomingEvents.length}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center space-x-3">
            <div className="p-3 rounded-full bg-yellow-100">
              <CalendarIcon className="w-6 h-6 text-yellow-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600">Planning</p>
              <p className="text-2xl font-bold text-gray-900">
                {planningEvents.length}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center space-x-3">
            <div className="p-3 rounded-full bg-green-100">
              <AlertCircleIcon className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600">Completed</p>
              <p className="text-2xl font-bold text-gray-900">
                {completedEvents.length}
              </p>
            </div>
          </div>
        </div>
      </div>
      {/* Events List */}
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="p-6 border-b">
          <h2 className="text-xl font-semibold text-gray-900">
            Events Timeline
          </h2>
        </div>
        <div className="p-6">
          <div className="space-y-6">
            {events.map(event => <div key={event.id} className="flex items-start space-x-4 p-4 border rounded-lg">
                <div className={`p-2 rounded-full ${event.status === 'Upcoming' ? 'bg-blue-100' : event.status === 'Planning' ? 'bg-yellow-100' : 'bg-green-100'}`}>
                  <CalendarIcon className={`w-5 h-5 ${event.status === 'Upcoming' ? 'text-blue-600' : event.status === 'Planning' ? 'text-yellow-600' : 'text-green-600'}`} />
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <h3 className="font-medium text-gray-900">{event.title}</h3>
                    <span className={`px-2 py-1 text-xs rounded-full ${event.status === 'Upcoming' ? 'bg-blue-100 text-blue-800' : event.status === 'Planning' ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'}`}>
                      {event.status}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mt-1">
                    {event.description}
                  </p>
                  <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500">
                    <span>{event.date}</span>
                    <span>•</span>
                    <span>{event.type}</span>
                  </div>
                </div>
              </div>)}
          </div>
        </div>
      </div>
    </div>;
}